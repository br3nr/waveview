// pages/_app.js
import { ChakraProvider, useColorMode } from '@chakra-ui/react'
import '../styles/global.css';
import { useRouter } from 'next/router';

function MyApp({ Component, pageProps }) {
  const router = useRouter();

  return (
    <ChakraProvider>
          <Component {...pageProps} key={router.asPath}/>
    </ChakraProvider>
  )
}

export default MyApp