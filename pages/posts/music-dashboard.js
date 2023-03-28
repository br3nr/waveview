import { useState, useEffect } from 'react';
import { Grid, GridItem, Button, Text, List, ListItem, ListIcon, Select, Flex } from '@chakra-ui/react';
import Nav from '../../components/navbar';
import MusicQueue from '../../components/music_queue';
import ThumbnailImage from '../../components/thumbnail_image';
import MarqueeText from '../../components/marquee_text';
import PlayControls from '../../components/play_controls';
import _ from 'lodash';
import Cookies from "js-cookie";
import { useRouter } from 'next/router';
import { RiDiscordFill } from 'react-icons/ri';

function MusicDashboard() {
  const [thumbnailUrl, setThumbnailUrl] = useState('/images/default.png');
  const [songState, setSongState] = useState("No song is playing.");
  const [selectedServer, setSelectedServer] = useState(null);
  const [voiceChannels, setVoiceChannels] = useState([{}]);
  const [trackQueue, setTrackQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userInformation, setUserInformation] = useState({});
  const router = useRouter();
  const [serverList, setServerList] = useState([{}]);
  const [serverIcon, setServerIcon] = useState("https://www.svgrepo.com/show/353655/discord-icon.svg");

  function handleServerClick(server) {
    props.handleServerClick(server);
    setServerIcon(server.icon);

  }

  async function onMenuClick() {

  }

  onMenuClick();

  useEffect(() => {
    const fetchData = async () => {
      // check if cookie exists
      const sessionId = Cookies.get("session_id");
      if (sessionId) {
        const response = await fetch(`/auth/login/${sessionId}`);

        if (!response.ok) {
          router.push('/');
        } else {
          const userJson = await response.json();
          const serverUrl = `/get_servers/${userJson.id}`;
          setUserInformation(userJson);

          const userServers = await (await fetch(serverUrl)).json();
          setServerList(userServers);
        }
      } else {
        router.push('/');
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  async function handleJoinServer(vc_id) {
    const url = `/join_vc/${selectedServer.id}/${vc_id}`;
    const response = await fetch(url);
    if (response.ok) {
      console.log("ok")
    }
    await handleServerClick(selectedServer)
  }

  async function handleServerClick(server) {
    console.log(server.id);
    const response = await fetch(`/get_vc/${server.id}`);
    const servers = await response.json();
    setVoiceChannels(servers);
    setSelectedServer(server);
  }

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:5090/ws');
    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      setSongState(data.title);
      setThumbnailUrl(data.thumbnail);
      setTrackQueue(data.queue);
    });

    return () => {
      socket.close();
    };
  }, []);

  return (
    <>
      <Nav handleServerClick={handleServerClick} currentUser={userInformation} />
      <br />

      <Grid templateColumns="repeat(3, 1fr)" gap={6}>
        <GridItem colSpan={1}>
          <Select width="60%" paddingLeft={5}>
            <option selected hidden disabled value="">-- Select a Discord server --</option>
            {serverList?.map((server) => (
              <option key={server.id} value={server.id} onClick={() => handleServerClick(server)}>
                {server.name}
              </option>
            ))}
          </Select>
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
                    {server.is_connected ? <RiDiscordFill/> : null}
                  </Flex>
                </Button>
              </ListItem>
            ))}
          </List>
        </GridItem>
        <GridItem colSpan={1}>
          <ThumbnailImage thumbnailUrl={thumbnailUrl} />
          <MarqueeText songState={songState} />
          <PlayControls />
        </GridItem>
        <GridItem colSpan={1}>
          <Text as='b' paddingLeft="10px">Song Queue</Text>
          <MusicQueue setTrackQueue={setTrackQueue} trackQueue={trackQueue} />
        </GridItem>
      </Grid>
    </>
  );
}

export default MusicDashboard;