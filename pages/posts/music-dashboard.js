import Link from 'next/link';
import Script from 'next/script';
import { Grid, GridItem, Button, Flex, Box, Image, Text, useColorMode } from '@chakra-ui/react'
import { useState, useEffect } from 'react';
import { MdPlaylistRemove } from 'react-icons/md'
import React from 'react';
import ThumbnailImage from '../../components/thumbnail_image';
import MarqueeText from '../../components/marquee_text';
import PlayControls from '../../components/play_controls';
import _ from 'lodash';
import { Spinner } from '@chakra-ui/react';
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import Nav from '../../components/navbar'

function MusicDashboard() {

  const [thumbnailUrl, setThumbnailUrl] = useState('/images/default.png')
  const [songState, setSongState] = useState("No song is playing.");
  const [trackQueue, setTrackQueue] = useState([]);
  const [removedTrackIds, setRemovedTrackIds] = useState([]);

  const removeTrack = async (track) => {
    setRemovedTrackIds([...removedTrackIds, track.uuid]);
    const url = `/remove_track/${track.uuid}`;
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
      <Nav/>
      <br/>
      <Grid templateColumns="repeat(3, 1fr)" gap={6}>
        <GridItem colSpan={1} >
         
        </GridItem>

        <GridItem colSpan={1} >
          <ThumbnailImage thumbnailUrl={thumbnailUrl} />
          <MarqueeText songState={songState} />
          <PlayControls />
        </GridItem>

        <GridItem colSpan={1} >
          <Text as='b' paddingLeft="10px">Song Queue</Text>
          <Flex flexDirection="column" >
            {trackQueue.map((track) => (
              <Flex key={track.id} borderRadius="50px" alignItems="center" width={550} margin="10px" >
                <Flex w="80%" alignItems="center">
                  <Image
                    src={track.thumbnail}
                    alt={track.title}
                    boxSize="50px"
                    objectFit="cover"
                    borderRadius="10px"
                  />
                  <Text
                    marginLeft="15px"
                    marginRight="0px"
                    as='h2'
                    size='md'
                    noOfLines={1}
                  >
                    {track.title}
                  </Text>
                </Flex>
                <Flex w="20%">
                  <Button 
                    height="50px"
                    borderRadius="50px"
                    onClick={() => removeTrack(track)} marginLeft="auto">
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