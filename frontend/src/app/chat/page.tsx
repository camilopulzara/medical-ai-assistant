"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./chat.module.css";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

// Componente para renderizar timestamp solo en cliente
function TimestampRenderer({ timestamp }: { timestamp: string }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span className={styles.timestamp}>--:--</span>;
  }

  return (
    <span className={styles.timestamp}>
      {new Date(timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })}
    </span>
  );
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "¡Hola! Soy tu asistente médico. ¿En qué puedo ayudarte hoy? Puedo consultar tus citas, documentos médicos, historial y responder preguntas sobre tu salud.",
      timestamp: new Date().toISOString(),
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [patientId, setPatientId] = useState(12); // Usar ID del paciente disponible
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll al último mensaje
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Crear sesión al cargar la página
  useEffect(() => {
    const createSession = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/chat/sessions`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ patient_id: patientId }),
        });

        if (response.ok) {
          const data = await response.json();
          setSessionId(data.session_id);
        }
      } catch (error) {
        console.error("Error creating session:", error);
      }
    };

    createSession();
  }, [patientId]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/api/chat/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          patient_id: patientId,
          message: input,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          role: "assistant",
          content: data.response || "No pude procesar tu solicitud.",
          timestamp: data.timestamp || new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorData = await response.json();
        const errorMessage: Message = {
          role: "assistant",
          content: `Error: ${errorData.detail || "No se pudo obtener respuesta. Intenta nuevamente."}`,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: `Error de conexion: ${error instanceof Error ? error.message : 'No se pudo conectar con el servidor'}.`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    router.push("/login");
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Medical AI Assistant</h1>
        <div className={styles.headerRight}>
          <span className={styles.patientInfo}>Paciente ID: {patientId}</span>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            Cerrar sesion
          </button>
        </div>
      </div>

      <div className={styles.chatWindow}>
        <div className={styles.messagesContainer}>
          {messages.map((msg, idx) => (
            <div key={idx} className={`${styles.message} ${styles[msg.role]}`}>
              <div className={styles.messageBubble}>
                <p>{msg.content}</p>
                <TimestampRenderer timestamp={msg.timestamp} />
              </div>
            </div>
          ))}
          {isLoading && (
            <div className={`${styles.message} ${styles.assistant}`}>
              <div className={styles.messageBubble}>
                <div className={styles.loadingDots}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className={styles.inputForm} onSubmit={handleSendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta o descripcion de sintomas..."
            disabled={isLoading}
            className={styles.input}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className={styles.sendBtn}
          >
            {isLoading ? "Enviando..." : "Enviar"}
          </button>
        </form>
      </div>
    </div>
  );
}
