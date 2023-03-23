import Head from 'next/head';
import styles from '../styles/Home.module.css';
import Link from 'next/link';
import { ChakraProvider, Image } from '@chakra-ui/react'
import { Button, Flex } from '@chakra-ui/react'

export default function Home() {


  async function handleClick()
  {
    const response = await fetch('https://discord.com/api/oauth2/authorize?client_id=748778849751400871&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds');
    const data = await response.json();
    console.log(data)
  }

  return (
    <div >
      <Flex direction={'column'} alignItems={'center'} justifyContent={'center'} height={'100vh'}>
      <Image margin={10} src="https://static1.personality-database.com/profile_images/4097d505c488482688656aad6cd03992.png" alt="Discord Logo" />
      <h1 className="title">
        <Link href="https://discord.com/api/oauth2/authorize?client_id=1077474383779606600&redirect_uri=http%3A%2F%2Flocalhost%3A5090%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds"><Button>Login</Button></Link>
      </h1>
      </Flex>
    </div>
  )
}
