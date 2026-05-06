type FulfillRequestCallback = (error: any, responsePayload: any) => void;
export type NotificationMethod = (...args: string[]) => void;

// https://worlds-slowest.dev/posts/rpc-using-websockets/
export default class Client {

    private readonly socket: WebSocket;
    private promisedRequests: Map<string, FulfillRequestCallback>;
    private readonly isSocketOpen: Promise<void>;
    protected readonly allowedNotificationMethods: Map<string, NotificationMethod> =
                                                                                  new Map<string, NotificationMethod>();

    public constructor(hostName: string = "localhost", portNumber: number) {
        this.promisedRequests = new Map<string, FulfillRequestCallback>()

        this.socket = new WebSocket(`ws://${hostName}:${portNumber}`);
        // receive() fires whenever socket receives a message
        this.socket.addEventListener("message", this.receive.bind(this));

        this.isSocketOpen =  new Promise((resolve, reject) => {
            this.socket.addEventListener("open", () => {
                resolve()
                console.log(`client.ts: connected to websocket at ws://${hostName}:${portNumber}!`)
            }, { once: true });
            this.socket.addEventListener("error",
              () => reject(new Error("client.ts: websocket failed to open")), { once: true });
        });
    }

    protected async send(requestType: string, requestArguments?: any[]): Promise<void> {
        await this.isSocketOpen;

        // https://stackoverflow.com/questions/9407892/how-to-generate-random-sha1-hash-to-use-as-id-in-node-js
        const requestID: string = crypto.randomUUID();

        return new Promise((resolve, reject) => {

            this.promisedRequests.set(requestID, (error: any, responsePayload: any) : void => {
                //#TODO add handling for pushes from the server here
                // #TODO if undefined is strict enough here
                if (error === undefined && responsePayload !== undefined) {
                    resolve(responsePayload);
                } else {
                    // error !== undefined || responsePayload === undefined
                    reject(new Error(
                        (error === undefined) ? "client.ts: server failed to process request" :
                                                `client.ts: server error (${error})`
                    ))
                }
            });

            this.socket.send(JSON.stringify(
                (requestArguments === undefined || requestArguments === null) ?
                  {type: "request", id: requestID, method: requestType} :
                  {type: "request", id: requestID, method: requestType, arguments: requestArguments}
            ));
        })
    }

    private receive(event: MessageEvent) : void {
       const response = JSON.parse(event.data);
       console.log(response)

       if (response.type === "response") {
           const fulfillRequestCallback: FulfillRequestCallback | undefined = this.promisedRequests.get(response.id);
           if (fulfillRequestCallback === undefined) return;
           this.promisedRequests.delete(response.id);
           fulfillRequestCallback(response.error, response.payload);
       } else if (response.type === "notification") {
           if (response.method === null || response.method === undefined) {
               throw new Error("client.ts#receive(): server sent malformed notification");
           }

           const method: NotificationMethod | undefined = this.allowedNotificationMethods.get(response.method);
           if (method === undefined) {
               throw new Error("client.ts#receive(): server sent invalid notification method");
           }

           if (!Array.isArray(response.arguments)){
               throw new Error("client.ts#receive(): server sent invalid arguments");
           }

           method(...response.arguments)
       } else {
           throw new Error("client.ts#receive(): server sent invalid response type");
       }
    }
}