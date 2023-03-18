import Link from 'next/link';
import Script from 'next/script';
import Layout from '../../components/layout';
import { Grid, GridItem, Button,  Flex, Box, Image } from '@chakra-ui/react'
import { useState, useEffect } from 'react';
import {  MdPlaylistRemove } from 'react-icons/md'
import React from 'react';
import ThumbnailImage from '../../components/thumbnail_image';
import MarqueeText from '../../components/marquee_text';
import PlayControls from '../../components/play_controls';
import _ from 'lodash';
import { Spinner } from '@chakra-ui/react';
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";


function MusicDashboard() {

  const [thumbnailUrl, setThumbnailUrl] = useState('/images/default.png')
  const [songState, setSongState] = useState("No song is playing.");
  const [trackQueue, setTrackQueue] = useState([]);
  const [removedTrackIds, setRemovedTrackIds] = useState([]);



  const removeTrack = async (track) => {
    setRemovedTrackIds([...removedTrackIds, track.uuid]);
    const url = `http://localhost:5090/remove_track/${track.uuid}`;
    await fetch(url);
    // remove the track from the queue
    const newQueue = trackQueue.filter((t) => t.uuid !== track.uuid);
    setTrackQueue(newQueue);
    // add the UUID of the removed track to the removedTrackIds array
  };

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
                  <Button onClick={() => removeTrack(track)}>
                    {removedTrackIds.includes(track.uuid) ? (
                      <Spinner size='xs' />
                    ) : (
                      <MdPlaylistRemove />
                    )}
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