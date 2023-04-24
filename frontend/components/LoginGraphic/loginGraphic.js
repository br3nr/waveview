import styles from "./Login.module.css";

function Login() {
  return (
    <div className={styles.body}>
      <div className={styles.screen}>
        <div className={styles.screenimage} />
        <div className={styles.screenoverlay} />
      </div>
    </div>
  );
}

export default Login;
