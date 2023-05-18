import Head from 'next/head';
import styles from '../styles/Home.module.css';
import Link from 'next/link';
import { ChakraProvider, Image } from '@chakra-ui/react'
import { Button, Center, Text, Flex, Box } from '@chakra-ui/react'
import Cookies from "js-cookie";
import { useRouter } from 'next/router'
import Login from '../components/LoginGraphic/loginGraphic';
import getConfig from 'next/config';

export default function Home() {
  const router = useRouter()
  const { publicRuntimeConfig } = getConfig();

  const redirectUri = process.env.NEXT_PUBLIC_REDIRECT_URI || publicRuntimeConfig.redirectUri;

  async function checkIsLoggedIn()
  {
    const sessionId = Cookies.get("session_id");
    if (sessionId) {
      const response = await fetch(`/auth/login/${sessionId}`);
      if (!response.ok) {
        router.push(redirectUri);
      } else {
        router.push('/posts/server-select')
      }
    } else {
      router.push(redirectUri);
    }
  }

  return (
    <div >
      <Flex direction={'column'} alignItems={'center'} justifyContent={'center'} height={'100vh'}>
      <h1 className="title">
        <Center>
          <Text marginBottom={3} fontFamily="mono">wavebot music dashboard</Text>
        </Center>
        <Box onClick={() => checkIsLoggedIn()}>
          <Login/>
        </Box>
      </h1>
      </Flex>
    </div>
  )
}
