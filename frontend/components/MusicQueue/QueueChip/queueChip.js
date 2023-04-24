import React from "react";
import { Flex, Image, Text, Spinner, useColorMode } from "@chakra-ui/react";
import { IconButton } from "@chakra-ui/react";
import { RxCross2 } from "react-icons/rx";

function QueueChip(props) {
  const { colorMode } = useColorMode();
  const bgColor = colorMode === "dark" ? "gray.900" : "gray.100";

  return (
    <>
      <Flex
        key={props.track.id}
        borderRightRadius="50px"
        borderLeftRadius="10px"
        alignItems="center"
        backgroundColor={bgColor}
        width={550}
      >
        <Flex w="80%" alignItems="center">
          <Image
            border="2px solid black"
            src={props.track.thumbnail}
            alt={props.track.title}
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
            {props.track.title}
          </Text>
        </Flex>
        <Flex
          w="20%"
          alignItems="center"
          justifyContent="center"
          marginRight="3px"
        >
          {props.removedTrackIds.includes(props.track.uuid) ? (
            <IconButton
              height="40px"
              width="40px"
              borderRadius="50px"
              background="transparent"
              onClick={() => removeTrack(props.track)}
              marginLeft="auto"
              variant="link"
              icon={<Spinner width="15px" height="15px" />}
              align="center" // Add align prop to align vertically
            />
          ) : (
            <IconButton
              height="40px"
              width="40px"
              border="2px solid primary"
              variant="outline"
              borderRadius="50px"
              background="transparent"
              onClick={() => props.removeTrack(props.track)}
              marginLeft="auto"
              icon={<RxCross2 width="15px" height="15px" />}
              align="center" // Add align prop to align vertically
            ></IconButton>
          )}
        </Flex>
      </Flex>
    </>
  );
}

export default QueueChip;
