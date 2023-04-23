import React, { useState, memo, useRef, useEffect } from "react";
import {
  Input,
  InputGroup,
  InputRightElement,
  Image,
} from "@chakra-ui/react";
import { BsSearchHeart } from "react-icons/bs";

const SearchBar = memo(() => {
  const [value, setValue] = useState("");
  const [isSpotify, setIsSpotify] = useState(false);
  const searchInputRef = useRef(null);

  useEffect(() => {
    // Set focus back to search bar input element after each websocket update
    if (searchInputRef.current) {
      searchInputRef.current.focus();
    }
  });

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
      const url = `/play_song/${localStorage.getItem("serverId")}`;
      await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ url: value }),
      });
    }
  };

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
          paddingRight="10px"
          children={<BsSearchHeart size="20px" />}
        />
      )}
    </InputGroup>
  );
});

export default SearchBar;