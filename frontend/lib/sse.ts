/**
 * SSE connection helper for streaming audit events from the backend.
 *
 * All events come through EventSource.onmessage (no named events)
 * to avoid conflicts with EventSource's built-in "error" event.
 */

export interface StreamEvent {
    type: "info" | "success" | "warning" | "error" | "progress" | "complete";
    message: string;
    timestamp: string;
    data?: Record<string, unknown>;
    stream_type?: "instant" | "typing";
}

export interface SSEOptions {
    onEvent: (event: StreamEvent) => void;
    onComplete?: (data: Record<string, unknown>) => void;
    onError?: (error: string) => void;
}

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

/**
 * Connect to an SSE stream from the backend.
 * Returns a cleanup function to close the connection.
 */
export function connectSSE(url: string, options: SSEOptions): () => void {
    const fullUrl = `${API_BASE}${url}`;
    const eventSource = new EventSource(fullUrl);

    // All events come through onmessage (no named event types)
    eventSource.onmessage = (event: MessageEvent) => {
        try {
            const parsed: StreamEvent = JSON.parse(event.data);

            // Handle completion
            if (parsed.type === "complete") {
                if (options.onComplete) {
                    options.onComplete(parsed.data || {});
                }
                eventSource.close();
                return;
            }

            // Handle all other events
            options.onEvent(parsed);
        } catch {
            // Non-JSON message, ignore
        }
    };

    // Handle connection errors
    eventSource.onerror = () => {
        if (eventSource.readyState === EventSource.CLOSED) {
            return; // Normal close after complete
        }
        if (options.onError) {
            options.onError("Connection to server lost");
        }
        eventSource.close();
    };

    // Return cleanup function
    return () => {
        eventSource.close();
    };
}

/**
 * Start a streaming audit for the given URL.
 */
export function startAuditStream(url: string, options: SSEOptions): () => void {
    const encodedUrl = encodeURIComponent(url);
    return connectSSE(`/api/audit/stream?url=${encodedUrl}`, options);
}
