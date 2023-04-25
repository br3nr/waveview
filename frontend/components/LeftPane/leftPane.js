import {
  Flex,
  List,
  ListItem,
  Button,
  IconButton,
  Box,
  Text,
  Tooltip,
  useColorMode,
  Icon,
} from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { RxCross2 } from "react-icons/rx";

function leftPane() {
  const [voiceChannels, setVoiceChannels] = useState([{}]);
  const [voiceChannel, setVoiceChannel] = useState();
  const [isHovered, setIsHovered] = useState({});
  const selectedServerId = localStorage.getItem("serverId");
  const { colorMode } = useColorMode();
  const bgColor = colorMode === "dark" ? "white" : "black";

  useEffect(() => {
    if (localStorage.getItem("serverId")) {
      const fetchData = async () => {
        const response = await fetch(`/get_vc/${selectedServerId}`);
        const servers = await response.json();
        setVoiceChannels(servers);
      };
      fetchData();
    }
  }, [voiceChannel]);

  async function handleJoinServer(vc_id) {
    const url = `/join_vc/${selectedServerId}/${vc_id}`;
    const response = await fetch(url);
    if (response.ok) {
      setVoiceChannel(vc_id);
    }
  }

  async function handleDisconnect(event, vc_id) {
    event.stopPropagation();
    event.preventDefault();
    const url = `/leave_vc/${selectedServerId}/${vc_id}`;
    const response = await fetch(url);
    if (response.ok) {
      // give the backend time to disconnect
      setTimeout(() => {
        setVoiceChannel(null);
      }, 500);
    }
  }

  return (
    <>
      <Box marginLeft={5} marginTop={4} width="100%" height="800px">
        <Text as="b" paddingLeft={5} paddingTop={5}>
          Channels:
        </Text>
        <List paddingLeft={5} paddingTop={3} spacing={3}>
          {voiceChannels?.map((server) => (
            <ListItem key={server.vc_id}>
              <Button
                paddingLeft={2}
                paddingRight={0}
                background="transparent"
                onMouseEnter={() => setIsHovered({ [server.vc_id]: true })}
                onMouseLeave={() => setIsHovered({ [server.vc_id]: false })}
              >
                <Flex
                  _hover={{ backgroundColor: "gray." }}
                  onClick={() => handleJoinServer(server.vc_id)}
                  alignItems="center"
                  width={250}
                  height={10}
                >
                  <Flex>
                    <Icon viewBox="0 0 24 24" width="24px" height="24px" color="red"> 
                      <path
                        d="M11.383 3.07904C11.009 2.92504 10.579 3.01004 10.293 3.29604L6 8.00204H3C2.45 8.00204 2 8.45304 2 9.00204V15.002C2 15.552 2.45 16.002 3 16.002H6L10.293 20.71C10.579 20.996 11.009 21.082 11.383 20.927C11.757 20.772 12 20.407 12 20.002V4.00204C12 3.59904 11.757 3.23204 11.383 3.07904ZM14 5.00195V7.00195C16.757 7.00195 19 9.24595 19 12.002C19 14.759 16.757 17.002 14 17.002V19.002C17.86 19.002 21 15.863 21 12.002C21 8.14295 17.86 5.00195 14 5.00195ZM14 9.00195C15.654 9.00195 17 10.349 17 12.002C17 13.657 15.654 15.002 14 15.002V13.002C14.551 13.002 15 12.553 15 12.002C15 11.451 14.551 11.002 14 11.002V9.00195Z"
                        fill={server.is_connected ? "#43b581" : bgColor}
                      />
                    </Icon>
                  </Flex>
                  <Flex width="90%" alignItems="center">
                    <Text paddingLeft={3} paddingTop={1}>
                      {server.vc_name}
                    </Text>
                  </Flex>
                  <Flex>
                    {server.is_connected & isHovered[server.vc_id] ? (
                      <Tooltip
                        label="disconnect"
                        placement="top"
                        hasArrow
                        bg="gray.900"
                        color="gray.100"
                      >
                        <IconButton
                          variant="link"
                          backgroundColor="transparent"
                          borderRadius="50px"
                          onClick={(event) =>
                            handleDisconnect(event, server.vc_id)
                          }
                          sx={{
                            "& svg:hover": {
                              color: "red.500",
                            },
                          }}
                          icon={<RxCross2 />}
                        ></IconButton>
                      </Tooltip>
                    ) : null}
                  </Flex>
                </Flex>
              </Button>
            </ListItem>
          ))}
        </List>
      </Box>
    </>
  );
}

export default leftPane;

/**
 * 
 * <Button
                background="trans"
                alignItems="center"
                flexDirection="row" // align items horizontally
                justifyContent="flex-start" // align items to the left
                paddingLeft={3}
                width={275}
                onClick={() => handleJoinServer(server.vc_id)}
              >
                <Flex alignItems="center">
                  {server.vc_name}
                  {server.is_connected ? <RiDiscordFill /> : null}
                </Flex>
              </Button>
 */
