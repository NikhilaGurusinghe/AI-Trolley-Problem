
// TODO how to ensure that sends are only sent when the socket has connected?
//  perhaps block until it has connected as we are only connecting once?
// TODO should we block until we receive a message?

import {randomBytes} from "node:crypto";

type FulfillRequestCallback = (error: any, responsePayload: any) => void

// https://worlds-slowest.dev/posts/rpc-using-websockets/
export default class Client {

    private readonly socket: WebSocket;
    private promisedRequests: Map<String, FulfillRequestCallback>;
    private readonly isSocketOpen: Promise<void>;

    public constructor(hostName: string = "localhost", portNumber: number) {
        this.promisedRequests = new Map<String, FulfillRequestCallback>()

        this.socket = new WebSocket(`ws://${hostName}:${portNumber}`);
        // receive fires whenever socket receives a message
        this.socket.addEventListener("message", this.receive.bind(this));

        this.isSocketOpen =  new Promise((resolve, reject) => {
            this.socket.addEventListener("open", () => resolve, { once: true });
            this.socket.addEventListener("error",
              () => reject(new Error("client.ts: websocket failed to open")), { once: true });
        });
    }

    public async send(requestType: String, requestArguments?: any[]): Promise<void> {
        await this.isSocketOpen;

        // https://stackoverflow.com/questions/9407892/how-to-generate-random-sha1-hash-to-use-as-id-in-node-js
        const requestID: String = randomBytes(20).toString("hex");

        return new Promise((resolve, reject) => {

            this.promisedRequests.set(requestID, (error: any, responsePayload: any) : void => {
                // #TODO if undefined is strict enough here
                if (error === undefined || error === null) {
                    reject(new Error("client.ts: server failed to process request"))
                } else {
                    resolve(responsePayload);
                }
            });

            this.socket.send(JSON.stringify(
                (requestArguments === undefined) ? {requestID, requestType} : {requestID, requestType, requestArguments}
            ));
        })
    }

    public receive(event: MessageEvent) : void {
       let response = JSON.parse(event.data);
       let fulfillRequestCallback: FulfillRequestCallback | undefined = this.promisedRequests.get(response.id);
       if (fulfillRequestCallback == undefined) return;
       this.promisedRequests.delete(response.id);
       fulfillRequestCallback(response.error, response.payload);
    }
}