import { Box, Center, Button, Icon } from "@chakra-ui/react";
import { FaPlay, FaPause, FaStepForward } from "react-icons/fa";
import React from "react";
import { useState } from "react";

function PlayControls(props) {
  const [buttonState, setButtonState] = useState("pause");

  async function handleClick() {
    setButtonState(buttonState === "play" ? "pause" : "play");
    if (buttonState == "pause") {
      const response = await fetch(`/pause/${props.selectedServer}`);
    } else {
      const response = await fetch(`/resume/${props.selectedServer}`);
    }
  }

  async function skipSong() {
    await fetch(`/skip/${props.selectedServer}`);
    setButtonState("pause");
  }

  return (
    <>
      <Center paddingTop="10px">
        <Box paddingRight={10}>
          <Button onClick={handleClick}>
            {buttonState === "play" ? (
              <Icon as={FaPlay} />
            ) : (
              <Icon as={FaPause} />
            )}
          </Button>
        </Box>
        <Button onClick={skipSong}>
          <Icon as={FaStepForward} />
        </Button>
      </Center>
      <Center marginTop={20}></Center>
    </>
  );
}

export default PlayControls;