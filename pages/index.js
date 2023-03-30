import Head from 'next/head';
import styles from '../styles/Home.module.css';
import Link from 'next/link';
import { ChakraProvider, Image } from '@chakra-ui/react'
import { Button, Center, Text, Flex, Box } from '@chakra-ui/react'
import Cookies from "js-cookie";
import { useRouter } from 'next/router'
import Login from '../components/Login';
export default function Home() {
  const router = useRouter()


  async function handleClick()
  {
    const response = await fetch('https://discord.com/api/oauth2/authorize?client_id=748778849751400871&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds');
    const data = await response.json();
    console.log(data)
  }

  async function checkIsLoggedIn()
  {
    //
    const session_id = Cookies.get("session_id");

    if (session_id) {
      router.push('/posts/music-dashboard')
      console.log(session_id);
    }
    else
    {
      // redirect to login page
      router.push('https://discord.com/api/oauth2/authorize?client_id=1077474383779606600&redirect_uri=http%3A%2F%2Flocalhost%3A5090%2Fauth%2Fredirect&response_type=code&scope=identify%20guilds')
    }


    //const response = await fetch('http://localhost:5090/auth/login');
    //const data = await response.json();
    //console.log(data)
    //      <Image margin={10} src="https://static1.personality-database.com/profile_images/4097d505c488482688656aad6cd03992.png" alt="Discord Logo" />

  }

  return (
    <div >
      <Flex direction={'column'} alignItems={'center'} justifyContent={'center'} height={'100vh'}>
      <h1 className="title">
        <Center>
          <Text marginBottom={3} fontFamily="mono">br3nr bot</Text>
        </Center>
        <Box onClick={() => checkIsLoggedIn()}>
          <Login/>
        </Box>
      </h1>
      </Flex>
    </div>
  )
}
