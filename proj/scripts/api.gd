extends Node
## Autoload "Api": conversa com o backend (cadastro, login, progresso no banco e relatório de erros).
## O jogo continua funcionando sem servidor: em modo convidado ou sem conexão, o save local em JSON é usado.

signal auth_changed

const CONFIG_PATH := "user://rato_config.json"
const SESSION_PATH := "user://rato_sessao.json"
const TIMEOUT := 4.0

var base_url: String = "http://127.0.0.1:8000"
var token: String = ""
var player: Dictionary = {}          # {id, nome, email}
var guest: bool = false              # escolheu jogar sem conta
var online: bool = true              # último contato com o servidor deu certo?
var queue: Array = []                # erros ainda não enviados
var pending_progress: bool = false   # save local mais novo que o do servidor
var _flushing: bool = false
var _push_busy: bool = false
var _push_again: bool = false
var _latest: Dictionary = {}


func _ready() -> void:
	var env := OS.get_environment("RATO_API")
	if env != "":
		base_url = env
	elif FileAccess.file_exists(CONFIG_PATH):
		var cfg = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
		if typeof(cfg) == TYPE_DICTIONARY and str(cfg.get("api_url", "")) != "":
			base_url = str(cfg["api_url"])
	base_url = base_url.rstrip("/")


func logged_in() -> bool:
	return token != ""


func player_name() -> String:
	return str(player.get("nome", ""))


# ------------------------------------------------------------------ HTTP
## Faz uma requisição e devolve {ok, status, data}. status 0 = servidor inacessível.
func request(method: HTTPClient.Method, path: String, body = null) -> Dictionary:
	var http := HTTPRequest.new()
	http.timeout = TIMEOUT
	add_child(http)
	var headers := PackedStringArray(["Content-Type: application/json"])
	if token != "":
		headers.append("Authorization: Bearer " + token)
	var payload: String = "" if body == null else JSON.stringify(body)
	var err := http.request(base_url + path, headers, method, payload)
	if err != OK:
		http.queue_free()
		online = false
		return {"ok": false, "status": 0, "data": {"erro": "Não foi possível conectar ao servidor."}}
	var res: Array = await http.request_completed
	http.queue_free()
	var status: int = int(res[1]) if int(res[0]) == HTTPRequest.RESULT_SUCCESS else 0
	var data = null
	var txt: String = (res[3] as PackedByteArray).get_string_from_utf8()
	if txt != "":
		data = JSON.parse_string(txt)
	if status == 0:
		online = false
		data = {"erro": "Servidor indisponível. Inicie o backend ou jogue offline."}
	else:
		online = true
	return {"ok": status >= 200 and status < 300, "status": status, "data": data}


func _error_text(r: Dictionary) -> String:
	if typeof(r["data"]) == TYPE_DICTIONARY and r["data"].has("erro"):
		return str(r["data"]["erro"])
	return "Erro inesperado (%d)." % int(r["status"])


# ------------------------------------------------------------------ conta
## Cria a conta. Devolve "" se deu certo ou a mensagem de erro.
func register(nome: String, email: String, senha: String) -> String:
	var r := await request(HTTPClient.METHOD_POST, "/api/cadastro", {"nome": nome, "email": email, "senha": senha})
	if not r["ok"]:
		return _error_text(r)
	await _start_session(r["data"])
	return ""


func login(email: String, senha: String) -> String:
	var r := await request(HTTPClient.METHOD_POST, "/api/login", {"email": email, "senha": senha})
	if not r["ok"]:
		return _error_text(r)
	await _start_session(r["data"])
	return ""


func _start_session(d: Dictionary) -> void:
	token = str(d["token"])
	player = d["jogador"]
	guest = false
	_load_pending()
	_save_session()
	await sync_progress()
	flush_queue()
	auth_changed.emit()


## Reabre a sessão guardada da última vez. Devolve true se o servidor ainda a aceita.
func restore_session() -> bool:
	if not FileAccess.file_exists(SESSION_PATH):
		return false
	var s = JSON.parse_string(FileAccess.get_file_as_string(SESSION_PATH))
	if typeof(s) != TYPE_DICTIONARY or not s.has("token") or not s.has("jogador"):
		return false
	if str(s.get("url", "")) != base_url:
		return false
	token = str(s["token"])
	player = s["jogador"]
	var r := await request(HTTPClient.METHOD_GET, "/api/progresso")
	if not r["ok"]:
		if r["status"] == 401:
			_clear_session()
		token = ""
		player = {}
		return false
	guest = false
	_load_pending()
	await sync_progress(r["data"])
	flush_queue()
	auth_changed.emit()
	return true


func logout() -> void:
	if token != "":
		await request(HTTPClient.METHOD_POST, "/api/logout", {})
	_clear_session()
	token = ""
	player = {}
	queue = []
	guest = false
	auth_changed.emit()


func play_as_guest() -> void:
	token = ""
	player = {}
	guest = true
	auth_changed.emit()


func _save_session() -> void:
	var f := FileAccess.open(SESSION_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"url": base_url, "token": token, "jogador": player}))


func _clear_session() -> void:
	if FileAccess.file_exists(SESSION_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SESSION_PATH))


# ------------------------------------------------------------------ progresso
## Depois do login: o save do servidor vira o save local (a menos que haja save local mais novo).
func sync_progress(server_data = null) -> void:
	if pending_progress and FileAccess.file_exists(Game.save_path()):
		var local = JSON.parse_string(FileAccess.get_file_as_string(Game.save_path()))
		if typeof(local) == TYPE_DICTIONARY:
			push_progress(local)
			return
	if server_data == null:
		var r := await request(HTTPClient.METHOD_GET, "/api/progresso")
		if not r["ok"]:
			return
		server_data = r["data"]
	if typeof(server_data) == TYPE_DICTIONARY and bool(server_data.get("existe", false)):
		var save := {"room": server_data["room"], "hp": server_data["hp"], "inv": server_data["inv"],
			"flags": server_data["flags"], "learned": server_data["learned"], "taken": server_data["taken"]}
		var f := FileAccess.open(Game.save_path(), FileAccess.WRITE)
		if f:
			f.store_string(JSON.stringify(save))
	elif FileAccess.file_exists(Game.save_path()):
		# conta nova/sem progresso no servidor: não herda o save de outra pessoa
		DirAccess.remove_absolute(ProjectSettings.globalize_path(Game.save_path()))


## Envia o save ao banco. Várias chamadas seguidas viram uma só (sempre vale a mais recente).
func push_progress(data: Dictionary) -> void:
	if not logged_in():
		return
	_latest = data
	if _push_busy:
		_push_again = true
		return
	_push_busy = true
	while true:
		_push_again = false
		var r := await request(HTTPClient.METHOD_PUT, "/api/progresso", _latest)
		pending_progress = not r["ok"]
		_save_pending()
		if not _push_again:
			break
	_push_busy = false


# ------------------------------------------------------------------ erros do jogador
func report_error(tipo: String, sala: int, detalhe: String = "") -> void:
	if not logged_in():
		return
	queue.append({"tipo": tipo, "sala": sala, "detalhe": detalhe.left(200),
		"quando": Time.get_datetime_string_from_system(true) + "Z"})
	_save_pending()
	flush_queue()


func flush_queue() -> void:
	if _flushing or queue.is_empty() or not logged_in():
		return
	_flushing = true
	while not queue.is_empty() and logged_in():
		var batch: Array = queue.slice(0, 50)
		var r := await request(HTTPClient.METHOD_POST, "/api/eventos", {"eventos": batch})
		if r["ok"] or (r["status"] >= 400 and r["status"] < 500 and r["status"] != 401 and r["status"] != 429):
			queue = queue.slice(batch.size())   # enviados (ou recusados por serem inválidos)
			_save_pending()
		else:
			break   # sem conexão: tenta de novo no próximo erro ou no próximo login
	_flushing = false


func _pending_path() -> String:
	return "user://rato_pendentes_u%d.json" % int(player.get("id", 0))


func _save_pending() -> void:
	if not player.has("id"):
		return
	var f := FileAccess.open(_pending_path(), FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"eventos": queue, "progresso": pending_progress}))


func _load_pending() -> void:
	queue = []
	pending_progress = false
	if FileAccess.file_exists(_pending_path()):
		var d = JSON.parse_string(FileAccess.get_file_as_string(_pending_path()))
		if typeof(d) == TYPE_DICTIONARY:
			queue = d.get("eventos", [])
			pending_progress = bool(d.get("progresso", false))


# ------------------------------------------------------------------ relatório
## Totais de erros por tipo, para mostrar no menu de pausa. Devolve {} se não der.
func fetch_summary() -> Dictionary:
	if not logged_in():
		return {}
	var r := await request(HTTPClient.METHOD_GET, "/api/relatorio?limite=1")
	if not r["ok"]:
		return {}
	var out := {"total": int(r["data"]["resumo"]["total"])}
	for t in r["data"]["resumo"]["por_tipo"]:
		out[str(t["codigo"])] = int(t["total"])
	return out


func open_report() -> void:
	if logged_in():
		OS.shell_open(base_url + "/relatorio#token=" + token)
	else:
		OS.shell_open(base_url + "/relatorio")
