import Link from "next/link";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <div className={styles.badge}>Medical AI Assistant</div>
        <h1>Un login claro para un sistema clinico confiable.</h1>
        <p>
          Accede al panel del asistente medico para gestionar pacientes,
          conversaciones y citas con enfoque humano.
        </p>
        <div className={styles.ctas}>
          <Link className={styles.primary} href="/login">
            Ir al login
          </Link>
          <a className={styles.secondary} href="http://localhost:8000/docs">
            Ver API
          </a>
        </div>
      </main>
    </div>
  );
}
