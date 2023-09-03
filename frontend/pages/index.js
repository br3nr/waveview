import { Center, Text, Flex, Box } from "@chakra-ui/react";
import { useRouter} from "next/router";
import Login from "../components/LoginGraphic/loginGraphic";
import getConfig from "next/config";
import {useEffect, useState } from "react";

export default function Home() {
  const router = useRouter();
  const { publicRuntimeConfig } = getConfig();
  const [redirectUri, setRedirectUri] = useState("");

  useEffect(() => {
    setRedirectUri(process.env.NEXT_PUBLIC_REDIRECT_URI || publicRuntimeConfig.redirectUri);
  },[]);

  async function checkIsLoggedIn() {

      const response = await fetch(`http://localhost:5090/auth/login`, { credentials: "include" });
      if (!response.ok) {
        router.push(redirectUri);
      } else {
        router.push("/server-select");
      }
  }

  return (
    <div>
      <title>waveview</title>
      <Flex
        direction={"column"}
        alignItems={"center"}
        justifyContent={"center"}
        height={"100vh"}
      >
        <h1 className="title">
          <Center>
            <Text marginBottom={3} fontFamily="mono">
              welcome to waveview
            </Text>
          </Center>
          <Box onClick={() => checkIsLoggedIn()}>
            <Login />
          </Box>
        </h1>
      </Flex>
    </div>
  );
}
