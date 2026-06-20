/**
 * useLiveStream Hook
 * Manages WebSocket connection to the live CCTV/RTSP stream endpoint.
 */

import { useState, useRef, useCallback } from "react";

export interface StreamFrame {
  frame: string;
  frame_number: number;
  vehicle_count: number;
  density_level: string;
  density_score: number;
  total_counted: number;
  counts_up: number;
  counts_down: number;
}

const WS_BASE =
  (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
    "http",
    "ws"
  ) + "/api/stream/live";

export function useLiveStream() {
  const [connected, setConnected] = useState(false);
  const [frameData, setFrameData] = useState<StreamFrame | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback((streamUrl: string) => {
    setError(null);
    const ws = new WebSocket(WS_BASE);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      ws.send(JSON.stringify({ url: streamUrl }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.error) {
        setError(data.error);
        return;
      }
      if (data.status === "stream_ended") {
        setConnected(false);
        return;
      }
      setFrameData(data);
    };

    ws.onerror = () => {
      setError("WebSocket connection error.");
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
    };
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    setConnected(false);
    setFrameData(null);
  }, []);

  return { connect, disconnect, connected, frameData, error };
}