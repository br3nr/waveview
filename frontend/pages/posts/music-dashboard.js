import { useState, useEffect, useRef } from "react";
import {
  Grid,
  GridItem,
  IconButton,
  Text,
  Box,
  Flex,
  AbsoluteCenter,
} from "@chakra-ui/react";
import Nav from "../../components/Navbar/navbar";
import MusicQueue from "../../components/MusicQueue/musicQueue";
import MusicPlayer from "../../components/MusicPlayer/musicPlayer";
import Cookies from "js-cookie";
import { useRouter } from "next/router";
import getConfig from "next/config";
import _ from "lodash";
import LeftPane from "../../components/LeftPane/leftPane";
import { MdPlaylistRemove } from "react-icons/md";
import { Spinner } from "@chakra-ui/react";

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
  const websocketUrl =
    process.env.NEXT_PUBLIC_WEBSOCKET_URL || publicRuntimeConfig.websocketUrl;

  const [loading, setLoading] = useState(true);

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

  function deleteQueueClick() {
    const url = `/api/delete_queue/${selectedServerId}`;
    fetch(url);
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
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const socket = new WebSocket(websocketUrl);
    socket.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      const track = data[localStorage.getItem("serverId")];

      if (track.title !== songState) {
        if (track.thumbnail === null) {
          if (trackQueueRef.current.length == 0) {
            console.log("no track in queue");
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
      setLoading(false);
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
      {loading ? (
        <Box width="100vw" height="100vh">
          <AbsoluteCenter>
            <Spinner width="50px" height="50px"></Spinner>
          </AbsoluteCenter>
        </Box>
      ) : (
        <Box>
          <Nav
            handleServerClick={handleServerClick}
            currentUser={userInformation}
          />
          <br />
          <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6}>
            <GridItem colSpan={1}>
              <Flex width="100%">
                <LeftPane selectedServerId={selectedServerId} />
              </Flex>
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
              <Flex alignItems="center">
                <Text as="b" paddingLeft="10px" paddingRight="10px">
                  Song Queue
                </Text>
                <IconButton
                  onClick={deleteQueueClick}
                  backgroundColor="transparent"
                >
                  <MdPlaylistRemove></MdPlaylistRemove>
                </IconButton>
              </Flex>
              <MusicQueue
                selectedServerId={selectedServerId}
                trackQueue={trackQueue}
                setTrackQueue={setTrackQueue}
              />
            </GridItem>
          </Grid>
        </Box>
      )}
    </>
  );
}

export default MusicDashboard;
