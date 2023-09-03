import React from "react";
import { useEffect, useState } from "react";
import Cookies from "js-cookie";
import { Box, Center, Flex, Image, Text } from "@chakra-ui/react";
import styles from "../../styles/ServerSelect.module.css";
import { useRouter } from "next/router";

function ServerSelect() {
  const [serverList, setServerList] = useState(null);
  const [loading, setLoading] = useState(true);
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
        const response = await fetch(`/auth/login/`, {
          credentials: "include",
        });

        if (!response.ok) {
          router.push("/");
        } else {
          const userJson = await response.json();
          const serverUrl = `/api/get_servers/${userJson.id}`;
          let userServers = await (await fetch(serverUrl)).json();

          userServers = userServers.map((server) => ({
            ...server,
            icon: server.icon === null ? "/discord.png" : server.icon,
          }));

          setServerList(userServers);
          setLoading(false);
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
        {serverList != null ? (
          <>
            {serverList.length > 0 ? (
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
                      </div>
                      <Text align="center">{server.name}</Text>
                    </Box>
                  );
                })}
              </Flex>
            ) : (
              <Text fontSize="3xl">No servers found.</Text>
            )}
          </>
        ) : (
          <Text fontSize="3xl">No servers found.</Text>
        )}
      </Center>
    </>
  );
}

export default ServerSelect;
