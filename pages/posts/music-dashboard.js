import { useState, useEffect } from 'react';
import { Grid, GridItem, Button, Text,  List, ListItem, ListIcon } from '@chakra-ui/react';
import { RiDiscordLine } from 'react-icons/ri';
import Nav from '../../components/navbar';
import MusicQueue from '../../components/music_queue';
import ThumbnailImage from '../../components/thumbnail_image';
import MarqueeText from '../../components/marquee_text';
import PlayControls from '../../components/play_controls';
import _ from 'lodash';
import Cookies from "js-cookie";
import { useToast } from "@chakra-ui/react";


function MusicDashboard() {
  const [thumbnailUrl, setThumbnailUrl] = useState('/images/default.png');
  const [songState, setSongState] = useState("No song is playing.");
  const [selectedServer, setSelectedServer] = useState(null);
  const [voiceChannels, setVoiceChannels] = useState([{}]);
  const [trackQueue, setTrackQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();
  const [userInformation, setUserInformation] = useState({});

  useEffect(() => {
    const userJSON = Cookies.get("current_user");
    if (userJSON) {
        
        // replace \054 with , 
        const formatJSON = userJSON.replace(/\\054/g, ',').replace(/\\/g, "");
        console.log(formatJSON)

        const userInformation = JSON.parse(formatJSON);
        setUserInformation(userInformation);
    } else {
        toast({
            title: "Error",
            description: "Access token not found",
            status: "error",
            duration: 9000,
            isClosable: true,
        });
    }
    setLoading(false);
  }, []);

  async function handleJoinServer(vc_id) {
    const url = `/join_vc/${selectedServer}/${vc_id}`;
    const response = await fetch(url);
    if (response.ok) {
      console.log("ok")
    }
  }

  async function handleServerClick(server) {
    console.log(server);
    const response = await fetch(`/get_vc/${server.id}`);
    const servers = await response.json();
    setVoiceChannels(servers);
    setSelectedServer(server.id);
    console.log(servers);
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
          <Text fontSize='lg' as='b' paddingLeft={5}>Available Channels:</Text>
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
                  <ListIcon as={RiDiscordLine} color='green.500' />
                  {server.vc_name}
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