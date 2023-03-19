// pages/_app.js
import { ChakraProvider, useColorMode } from '@chakra-ui/react'
import '../styles/global.css';
function MyApp({ Component, pageProps }) {
  return (
    <ChakraProvider>
          <Component {...pageProps} />
    </ChakraProvider>
  )
}

export default MyApp