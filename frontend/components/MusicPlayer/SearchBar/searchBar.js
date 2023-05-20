import React, { useState, memo, useRef } from "react";
import {
  Input,
  InputGroup,
  InputRightElement,
  Image,
  IconButton,
} from "@chakra-ui/react";
import { BsSearchHeart } from "react-icons/bs";
import { useToast } from "@chakra-ui/react";

const SearchBar = memo(() => {
  const [value, setValue] = useState("");
  const [isSpotify, setIsSpotify] = useState(false);
  const searchInputRef = useRef(null);
  const toast = useToast();

  const handleChange = (event) => {
    setValue(event.target.value);
    const regexPattern =
      /^((?:https?:\/\/)?(?:[a-z]+\.)?spotify\.com\/[a-zA-Z0-9/]+)$/;
    const regex = new RegExp(regexPattern);
    if (regex.test(event.target.value)) {
      setIsSpotify(true);
    } else {
      setIsSpotify(false);
    }
  };

  const handleKeyPress = async (event) => {
    if (event.key === "Enter") {
      setIsSpotify(false);
      setValue("");
      const url = `/api/play_song/${localStorage.getItem("serverId")}`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: value }),
      });
      if (!response.ok) {
        const responseJson = await response.json();
        toast({
          title: "Error",
          description: responseJson.detail,
          status: "error",
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  async function handleSearchClick() {
    setIsSpotify(false);
    setValue("");
    const url = `/api/play_song/${localStorage.getItem("serverId")}`;
    await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: value }),
    });
  }

  return (
    <InputGroup width="80%">
      <Input
        key="searchBar"
        placeholder="Search for music via query or url"
        onKeyPress={handleKeyPress}
        defaultValue={value}
        value={value}
        onChange={handleChange}
        ref={searchInputRef}
        onClick={handleKeyPress}
      />
      {isSpotify ? (
        <InputRightElement
          children={
            <Image
              boxSize="20px"
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Spotify_icon.svg/29px-Spotify_icon.svg.png"
            />
          }
        />
      ) : (
        <InputRightElement
          children={
            <IconButton
              onClick={handleSearchClick}
              backgroundColor="transparent"
            >
              <BsSearchHeart size="20px" />
            </IconButton>
          }
        />
      )}
    </InputGroup>
  );
});

export default SearchBar;
