import {
  Input,
  InputGroup,
  InputRightElement,
  Image,
  Center,
} from "@chakra-ui/react";
import { BsSearchHeart } from "react-icons/bs";
import React from "react";
import { useState } from "react";

function SearchBar(props) {
  const [value, setValue] = React.useState("");
  const [isSpotify, setIsSpotify] = useState(false);

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
      const url = `/play_song/${props.selectedServer}`;
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
    <InputGroup width="80%" >
      <Input
        placeholder="Search for music via query or url"
        onKeyPress={handleKeyPress}
        value={value}
        onChange={handleChange}
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
}

export default SearchBar;
