import Head from 'next/head';
import styles from '../styles/Home.module.css';
import Link from 'next/link';
import Image from 'next/image';
import { ChakraProvider } from '@chakra-ui/react'
import { Button } from '@chakra-ui/react'

export default function Home() {


  async function handleClick()
  {
    const response = await fetch('https://discord.com/api/oauth2/authorize?client_id=748778849751400871&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds');
    const data = await response.json();
    console.log(data)
  }

  return (
    <div className={styles.container}>
      <h1 className="title">
        <Link href="/posts/music-dashboard">Dashboard</Link>
      </h1>
      <h1 className="title">
        <Link href="https://discord.com/api/oauth2/authorize?client_id=748778849751400871&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds">Redirect</Link>
      </h1>
    </div>
  )
}
