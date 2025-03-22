class ServerMessageInterface:
    class Keys:
        Host = "host"
        SelectMesh = "select_mesh"
        UploadMesh = "upload_mesh"
        InitConnection = "init_connection"
        NumberClients = "nbr_clients"
        Viewer = "viewer"
        Success = "success"
        TramePort = "trame_port"

    class ReqSetMesh:
        MeshList = "mesh_list"
        NbrFrames = "nbr_frames"
        Width = "width"
        Height = "height"

    class RespSetMesh:
        Error = "error"
        RequestFiles = "request_files"
        RequestSpace = "request_space"


class ProxyMessageInterface:
    class Keys:
        Action = "action"
        ServerURL = "server_url"
        ServerID = "server_id"

    class Actions:
        Add = "add"
        Remove = "remove"


class EndpointsInterface:
    Protocol = "http"
    Localhost = f"{Protocol}://127.0.0.1"
    InitConnection = "/init_connection"
    SelectMesh = "/select_mesh"
    UploadMesh = "/upload_mesh"
    ClientsNumber = "/nbr_clients"
    KillServer = "/kill_server"
    SetViewer = "/set_viewer"
    KnownByManager = "/know_by_manager"

    class Proxy:
        UpdateAvailableServers = "/update_available_servers"
