import React from "react";
import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { Box, Center, Flex, Image, Text } from "@chakra-ui/react";
import styles from "../../styles/ServerSelect.module.css";
import { useRouter } from "next/router";

function ServerSelect() {
  const [serverList, setServerList] = useState([{}]);
  const router = useRouter();

  function handleServerClick(server) {
    router.push({
      pathname: "music-dashboard",
    });
    localStorage.setItem("serverId", server.id);
  }

  useEffect(() => {
    const fetchData = async () => {
      // check if cookie exists
      const sessionId = Cookies.get("session_id");
      if (sessionId) {
        const response = await fetch(`/auth/login/${sessionId}`);

        if (!response.ok) {
          router.push("/");
        } else {
          const userJson = await response.json();
          const serverUrl = `/get_servers/${userJson.id}`;
          const userServers = await (await fetch(serverUrl)).json();
          setServerList(userServers);
        }
      } else {
        router.push("/");
      }
    };
    fetchData();
  }, []);

  return (
    <>
      <Center h="100vh">
        <Flex>
          {serverList.map((server, index) => {
            return (
              <Box
                onClick={() => handleServerClick(server)}
                key={index}
                w="200px"
                h="200px"
                m="30px"
              >
                <div className={styles.div}>
                  <Image
                    src={server.icon}
                    w="200px"
                    h="200px"
                    borderRadius="10px"
                    objectFit="cover"
                  />
                  <Text align="center">{server.name}</Text>
                </div>
              </Box>
            );
          })}
        </Flex>
      </Center>
    </>
  );
}

export default ServerSelect;
