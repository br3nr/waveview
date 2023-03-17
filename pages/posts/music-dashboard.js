import Link from 'next/link';
import Script from 'next/script';
import Layout from '../../components/layout';
import { Grid, GridItem, Text, Heading, Button, Center, Flex, Box, Image, Icon, Container, ButtonSpinner } from '@chakra-ui/react'
import { useState, useEffect } from 'react';
import { FaPlay, FaPause, FaStepForward } from 'react-icons/fa'
import { MdOutlinePlaylistRemove } from 'react-icons/md'
import React from 'react';
import Marquee from "react-fast-marquee";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { SpinningCircles } from 'react-loading-icons'
import ThumbnailImage from '../../components/thumbnail_image';
import MarqueeText from '../../components/marquee_text';
import PlayControls from '../../components/play_controls';
import TrackQueue from '../../components/track_queue_element';
import _ from 'lodash';

function MusicDashboard() {

  const [thumbnailUrl, setThumbnailUrl] = useState('/images/default.png')
  const [isDeleting, setIsDeleting] = useState(false); // Add state variable for locking
  const [songState, setSongState] = useState("No song is playing.");
  const [isActive, setIsActive] = useState(false);
  const [trackQueue, setTrackQueue] = useState([]);


  const removeTrack = async (track) => {
    if (isDeleting) {
      // If a deletion is already in progress, return without doing anything
      return;
    }
  
    try {
      setIsDeleting(true); // Lock the deletion process
      setIsActive(!isActive);
  
      const url = `http://localhost:5090/remove_track/${track.id}`;
      await fetch(url);
  
      // Update the track queue
      const updatedQueue = trackQueue
        .filter((t) => t.id !== track.id)
        .map((t, index) => ({
          ...t,
          index: index + 1, // Update the index of each track in the array
        }));
      setTrackQueue(updatedQueue);
    } catch (error) {
      console.error(error);
    } finally {
      setIsDeleting(false); // Release the lock
    }
  };

  const debouncedRemoveTrack = _.debounce(removeTrack, 500);


  useEffect(() => {
    const socket = new WebSocket('ws://localhost:5090/ws');

    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data);
      setSongState(data.title)
      setThumbnailUrl(data.thumbnail)
      setTrackQueue((data.queue))
    });

    return () => {
      socket.close();
    };
  }, []);

  return (
    <>
      <h1>brennerbot / pandaden preview</h1>
      <Grid templateColumns="repeat(3, 1fr)" gap={6}>
        <GridItem colSpan={1} bg='white.500' />

        <GridItem colSpan={1} bg='white.500'>
          <ThumbnailImage thumbnailUrl={thumbnailUrl} />
          <MarqueeText songState={songState} />
          <PlayControls />
        </GridItem>

        <GridItem colSpan={1} bg='white.500'>
          <Flex flexDirection="column">
            {trackQueue.map((track) => (
              <Flex key={track.id} alignItems="center" margin="10px">
                <Flex w="80%">
                  <Image
                    src={track.thumbnail}
                    alt={track.title}
                    boxSize="50px"
                    objectFit="cover"
                  />
                  <Box
                    mt='1'
                    marginLeft="20px"
                    marginRight="20px"
                    as='h2'
                    size='md'
                    noOfLines={1}
                  >
                    {track.title}
                  </Box>
                </Flex>
                <Flex w="20%">
                  <Button key={track.id} onClick={() => debouncedRemoveTrack(track)}>
                    <MdOutlinePlaylistRemove />
                  </Button>
                </Flex>
              </Flex>
            ))}
          </Flex>
        </GridItem>
      </Grid>
    </>
  );
}

export default MusicDashboard;