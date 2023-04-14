import { Box, Center, Button, Icon } from "@chakra-ui/react";
import { FaPlay, FaPause, FaStepForward } from "react-icons/fa";
import React from "react";
import { useState } from "react";
import { Input, InputGroup, InputRightElement, Image } from "@chakra-ui/react";
import {BsSearchHeart} from "react-icons/bs"

function PlayControls(props) {
  const [buttonState, setButtonState] = useState("pause");
  const [spinning, setSpinning] = useState(0);
  const [value, setValue] = React.useState("");
  const [isSpotify, setIsSpotify] = useState(false);

  const handleChange = (event) => {
    setValue(event.target.value);
    const regexPattern = /^((?:https?:\/\/)?(?:[a-z]+\.)?spotify\.com\/[a-zA-Z0-9/]+)$/;
	const regex = new RegExp(regexPattern);
	console.log(regex.test(event.target.value))

    if (regex.test(event.target.value)) {
      setIsSpotify(true);
    }
	else
	{
		setIsSpotify(false);
	}

  };

  const handleKeyPress = async (event) => {
    if (event.key === "Enter") {
      setValue("");
      const url = `/play_song/${props.selectedServer}`;
      await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: value }),
      });
      console.log("Enter key pressed!");
      console.log(value);
    }
  };

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
      <Center >
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
      <Center marginTop={20}>
        <InputGroup width="80%" marginTop={15}>
          <Input
            placeholder="Search for music via query or url"
            onKeyPress={handleKeyPress}
            value={value}
            onChange={handleChange}
          />
          {isSpotify ? ( 
            <InputRightElement 
              children={
                <Image boxSize="20px" src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/29px-Spotify_icon.svg.png" />
              }
            />
          ) : (
            <InputRightElement paddingRight="10px"
              children={
				<BsSearchHeart size="20px"/>
			}
            />
          )}
        </InputGroup>
      </Center>
    </>
  );
}

export default PlayControls;
