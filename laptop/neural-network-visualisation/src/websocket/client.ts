
// TODO how to ensure that sends are only sent when the socket has connected?
//  perhaps block until it has connected as we are only connecting once?
// TODO should we block until we receive a message?

export default class Client {

    private readonly socket: WebSocket;
    private isReadyToSend: boolean = false;
    private lastReceivedMessage: JSON | undefined = undefined;

    public constructor(hostName: string = "localhost", portNumber: number) {
        this.socket = new WebSocket(`ws://${hostName}:${portNumber}`);
        this.socket.onopen = (): void => {
            this.isReadyToSend = true
        };
    }

    public send(data: any): boolean {
        if (!this.isReadyToSend) return false;
        this.socket.send(JSON.stringify(data));
        return true;
    }

    public receive(socket: WebSocket) {
        socket.addEventListener("message", ({ data }): void => {
            this.lastReceivedMessage = JSON.parse(data);
        })
    }

}