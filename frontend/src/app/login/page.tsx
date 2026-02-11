"use client";

import { useState } from "react";
import styles from "./login.module.css";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus("loading");
    setMessage("");

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || "No se pudo iniciar sesion.");
      }

      const data = await response.json();
      setStatus("success");
      setMessage(data?.message || "Login exitoso.");
    } catch (error) {
      const err = error as Error;
      setStatus("error");
      setMessage(err.message || "Error desconocido.");
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.header}>
          <span className={styles.kicker}>Acceso Clinico</span>
          <h1>Bienvenido de vuelta</h1>
          <p>Inicia sesion para continuar con la gestion de pacientes.</p>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <label className={styles.label}>
            Email
            <input
              type="email"
              name="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="tu@email.com"
              required
            />
          </label>

          <label className={styles.label}>
            Contrasena
            <input
              type="password"
              name="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="••••••••"
              required
            />
          </label>

          <button className={styles.submit} type="submit" disabled={status === "loading"}>
            {status === "loading" ? "Validando..." : "Iniciar sesion"}
          </button>
        </form>

        <div className={styles.footer}>
          <span className={styles.status} data-state={status}>
            {message || "Usa tus credenciales del sistema."}
          </span>
          <a className={styles.link} href="/">
            Volver al inicio
          </a>
        </div>
      </div>
    </div>
  );
}
