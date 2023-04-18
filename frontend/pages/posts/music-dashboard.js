import { useState, useEffect } from "react";
import {
  Grid,
  GridItem,
  Button,
  Text,
  List,
  ListItem,
  Flex,
} from "@chakra-ui/react";
import Nav from "../../components/Navbar/navbar";
import MusicQueue from "../../components/MusicQueue/musicQueue";
import MusicPlayer from "../../components/MusicPlayer/musicPlayer";
import Cookies from "js-cookie";
import { useRouter } from "next/router";
import { RiDiscordFill } from "react-icons/ri";

function MusicDashboard() {
  const router = useRouter();
  const [thumbnailUrl, setThumbnailUrl] = useState("/images/default2.png");
  const [songState, setSongState] = useState("No song is playing.");
  const [selectedServer, setSelectedServer] = useState();
  const [voiceChannels, setVoiceChannels] = useState([{}]);
  const [trackQueue, setTrackQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userInformation, setUserInformation] = useState({});
  const [serverList, setServerList] = useState([{}]);
  const [serverIcon, setServerIcon] = useState(
    "https://www.svgrepo.com/show/353655/discord-icon.svg"
  );
  const { serverId, setServerId } = useState();
  const [serverDetails, setServerDetails] = useState({});
  const [voiceChannel, setVoiceChannel] = useState();
  const [isLoaded, setIsLoaded] = useState(false);

  function handleServerClick(server) {
    props.handleServerClick(server);
    setServerIcon(server.icon);
  }

  useEffect(() => {
    const fetchData = async () => {
      setSelectedServer(localStorage.getItem("serverId"));
      // check if cookie exists
      const sessionId = Cookies.get("session_id");
      if (sessionId) {
        const response = await fetch(`/auth/login/${sessionId}`);
        if (!response.ok) {
          router.push("/");
        } else {
          const userJson = await response.json();
          const serverUrl = `/get_servers/${userJson.id}`;
          setUserInformation(userJson);
          const userServers = await (await fetch(serverUrl)).json();
          setServerList(userServers);
          setIsLoaded(true);
        }
      } else {
        router.push("/");
        setTimeout(() => {
          window.location.reload();
        }, 200);
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  // make a useEffect that checks if the cookie exists
  // if it does, fetch the user information
  // if it doesn't, redirect to the login page

  async function handleJoinServer(vc_id) {
    const url = `/join_vc/${selectedServer}/${vc_id}`;
    const response = await fetch(url);
    if (response.ok) {
      setVoiceChannel(vc_id);
    }
  }

  useEffect(() => {
    if (selectedServer) {
      const fetchData = async () => {
        const response = await fetch(`/get_vc/${selectedServer}`);
        const servers = await response.json();
        setVoiceChannels(servers);
      };
      fetchData();
    }
  }, [selectedServer, voiceChannel]);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:5090/ws");
    //const socket = new WebSocket('ws://45.32.191.6:5090/ws');
    socket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      const server = data[selectedServer];
      setSongState(server.title);
      setThumbnailUrl(server.thumbnail === null ? "/images/default2.png" : server.thumbnail);
      setTrackQueue(server.queue);
      setServerDetails(server);
    });

    return () => {
      socket.close();
    };
  }, [selectedServer]);

  return (
    <>
      <Nav
        handleServerClick={handleServerClick}
        currentUser={userInformation}
      />
      <br />
      <Grid templateColumns="repeat(3, 1fr)" gap={6}>
        <GridItem colSpan={1}>
          <List paddingLeft={5} paddingTop={1} spacing={3}>
            {voiceChannels?.map((server) => (
              <ListItem key={server.vc_id}>
                <Button
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
              </ListItem>
            ))}
          </List>
        </GridItem>
        <GridItem colSpan={1}>
          <MusicPlayer songState={songState} thumbnailUrl={thumbnailUrl} selectedServer={selectedServer} />
        </GridItem>
        <GridItem colSpan={1}>
          <Text as="b" paddingLeft="10px">
            Song Queue
          </Text>
          <MusicQueue
            selectedServer={selectedServer}
            trackQueue={trackQueue}
            setTrackQueue={setTrackQueue}
          />
        </GridItem>
      </Grid>
    </>
  );
}

export default MusicDashboard;
