import React, { useState, useCallback } from "react";
import {Flex, Image, Text, Spinner } from "@chakra-ui/react";
import { IconButton } from "@chakra-ui/react";
import { RxCross2 } from "react-icons/rx";
import styles from './musicQueue.module.css';

function MusicQueue(props) {
  const [removedTrackIds, setRemovedTrackIds] = useState([]);

  const removeTrack = useCallback(
    async (track) => {
      setRemovedTrackIds([...removedTrackIds, track.uuid]);
      const url = `/remove_track/${localStorage.getItem("serverId")}/${track.uuid}`;
      await fetch(url);
    },
    [removedTrackIds]
  );

  return (
    <>
      <Flex
        flexDirection="column"
        overflowY="scroll"
        width="100%"
        height="800px"
        marginTop="10px"
        className={styles.customScrollbar}
      >
        {props.trackQueue.map((track) => (
          <Flex
            key={track.id}
            borderRadius="50px"
            alignItems="center"
            width={550}
            margin="10px"
          >
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
                as="h2"
                size="md"
                noOfLines={1}
              >
                {track.title}
              </Text>
            </Flex>
            <Flex w="20%" alignItems="center" justifyContent="center">
              {removedTrackIds.includes(track.uuid) ? (
                <IconButton
                  height="40px"
                  width="40px"
                  borderRadius="50px"
                  background="transparent"
                  onClick={() => removeTrack(track)}
                  marginLeft="auto"
                  variant="link"
                  icon={<Spinner width="15px" height="15px" />}
                  align="center" // Add align prop to align vertically
                />
              ) : (
                <IconButton
                  height="40px"
                  width="40px"
                  variant="outline"
                  borderRadius="50px"
                  background="transparent"
                  onClick={() => removeTrack(track)}
                  marginLeft="auto"
                  icon={<RxCross2 width="15px" height="15px" />}
                  align="center" // Add align prop to align vertically
                ></IconButton>
              )}
            </Flex>
          </Flex>
        ))}
      </Flex>
    </>
  );
}

export default MusicQueue;