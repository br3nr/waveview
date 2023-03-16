import Link from 'next/link';
import Script from 'next/script';
import Layout from '../../components/layout';
import { Grid, GridItem, Text, Heading, Button, Center, Flex, Box, Image, Icon, Container } from '@chakra-ui/react'
import { useState, useEffect } from 'react';
import { FaPlay, FaPause, FaStepForward } from 'react-icons/fa'
import React from 'react';
import Marquee from "react-fast-marquee";

function MusicDashboard() {

  const [thumbnailUrl, setThumbnailUrl] = useState('/images/default.png')

  const [buttonState, setButtonState] = useState("pause");
  const [songState, setSongState] = useState("No song is playing.");

  const [trackQueue, setTrackQueue] = useState([]);


  async function handleClick() {
    if (buttonState == "pause") {
      const response = await fetch('/pause');
    } else {
      const response = await fetch('/resume');
    }
    setButtonState(buttonState === "play" ? "pause" : "play");
  }

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

  async function skipSong() {
    await fetch('/skip');
  }

  return (
    <>
      <h1>brennerbot / pandaden preview</h1>
      <Grid templateColumns="repeat(3, 1fr)" gap={6}>
        <GridItem colSpan={1} bg='white.500'/>
        <GridItem colSpan={1} bg='white.500'>

          <Center>
          {thumbnailUrl && (
            <Image
              src={thumbnailUrl}
              fallbackSrc="/images/default.png"
              style={{
                width: "600px",
                objectFit: "cover",
                objectPosition: "center",
              }}
            />
          )}
          </Center>

          <Center>
            <Marquee
              speed={60}
              gradientWidth={50}
              style={{
                width: "400px",
              }}
            >
              {songState}
            </Marquee>
          </Center>

          <Center>
          <Button onClick={handleClick}>
            {buttonState === "play" ? (
              <Icon as={FaPlay} />
            ) : (
              <Icon as={FaPause} />
            )}
          </Button>
          <Button onClick={skipSong}>
            <Icon as={FaStepForward} />
          </Button>
          </Center>
        </GridItem>

        <GridItem colSpan={1} bg='white.500'>          
            <Flex flexDirection="column">
              {trackQueue.map((item) => (
                <Flex
                  key={item.title}
                  alignItems="center"
                  margin="10px"
                >
                  <Image
                    src={item.thumbnail}
                    alt={item.title}
                    boxSize="50px"
                    objectFit="cover"
                  />
                  <Box marginLeft="20px">
                    <Heading
                      as="h2"
                      size="md"
                      style={{
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {item.title}
                    </Heading>
                    <Text>{item.title}</Text>
                  </Box>
                </Flex>
              ))}
            </Flex>
        </GridItem>
      </Grid>
    </>
  );
}

export default MusicDashboard;