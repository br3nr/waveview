import { useState, useEffect, useRef } from "react";
import {
  Grid,
  GridItem,
  Button,
  Text,
  List,
  Box,
  ListItem,
  Flex,
} from "@chakra-ui/react";
import Nav from "../../components/Navbar/navbar";
import MusicQueue from "../../components/MusicQueue/musicQueue";
import MusicPlayer from "../../components/MusicPlayer/musicPlayer";
import Cookies from "js-cookie";
import { useRouter } from "next/router";
import { RiDiscordFill } from "react-icons/ri";
import getConfig from "next/config";
import _ from "lodash";
import LeftPane from "../../components/LeftPane/leftPane";

function MusicDashboard() {
  const router = useRouter();
  const [thumbnailUrl, setThumbnailUrl] = useState("/images/default2.png");
  const [songState, setSongState] = useState("No song is playing.");
  const [selectedServerId, setSelectedServerId] = useState();
  const [trackQueue, setTrackQueue] = useState([]);
  const [userInformation, setUserInformation] = useState({});
  const [trackTime, setTrackTime] = useState([0, 0]);
  const { publicRuntimeConfig } = getConfig();
  const trackQueueRef = useRef([]);

  useEffect(() => {
    const serverId = localStorage.getItem("serverId");
    if (serverId) {
      setSelectedServerId(serverId);
    }
  }, []);

  function handleServerClick(server) {
    props.handleServerClick(server);
    setServerIcon(server.icon);
  }

  useEffect(() => {
    const fetchData = async () => {
      setSelectedServerId(localStorage.getItem("serverId"));
      const sessionId = Cookies.get("session_id");
      if (sessionId) {
        const response = await fetch(`/auth/login/${sessionId}`);
        if (!response.ok) {
          router.push("/");
        } else {
          const userJson = await response.json();
          setUserInformation(userJson);
        }
      } else {
        router.push("/");
        setTimeout(() => {
          window.location.reload();
        }, 200);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const websocketUrl = publicRuntimeConfig.websocketUrl;
    const socket = new WebSocket(websocketUrl);
    socket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      const track = data[localStorage.getItem("serverId")];

      if (track.title !== songState) {
        if (track.thumbnail === null) {
          if (trackQueueRef.current.length == 0) {
            console.log("no track in queue")
            setThumbnailUrl("/images/default2.png");
            setSongState(track.title);
          }
        } else {
          setThumbnailUrl(track.thumbnail);
          setSongState(track.title);
        }
      }
      // Check if track has changed via dnd, if so, update queue
      if (!_.isEqual(track.queue, trackQueueRef.current)) {
        trackQueueRef.current = track.queue;
      }
      setTrackTime([track.position, track.length]);
    });

    return () => {
      socket.close();
    };
  }, [selectedServerId]);

  useEffect(() => {
    console.log(trackQueueRef.current);
    setTrackQueue(trackQueueRef.current);
  }, [trackQueueRef.current]);

  return (
    <>
      <Box>
        <Nav
          handleServerClick={handleServerClick}
          currentUser={userInformation}
        />
        <br />
        <Grid templateColumns="repeat(3, 1fr)" gap={6}>
          <GridItem colSpan={1}>
            <LeftPane selectedServerId={selectedServerId} />
          </GridItem>
          <GridItem colSpan={1} paddingTop="15px">
            <MusicPlayer
              songState={songState}
              thumbnailUrl={thumbnailUrl}
              selectedServerId={selectedServerId}
              trackTime={trackTime}
            />
          </GridItem>
          <GridItem colSpan={1} paddingTop="15px">
            <Text as="b" paddingLeft="10px">
              Song Queue
            </Text>
            <MusicQueue
              selectedServerId={selectedServerId}
              trackQueue={trackQueue}
              setTrackQueue={setTrackQueue}
            />
          </GridItem>
        </Grid>
      </Box>
    </>
  );
}

export default MusicDashboard;
