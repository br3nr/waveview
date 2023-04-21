import { Box, Center, Button, Icon } from "@chakra-ui/react";
import { FaPlay, FaPause, FaStepForward } from "react-icons/fa";
import React from "react";
import { useState } from "react";
import { Input, InputGroup, InputRightElement, Image } from "@chakra-ui/react";
import { BsSearchHeart } from "react-icons/bs";
import Marquee from "react-fast-marquee";
import TrackImage from "./TrackImage/trackImage";
import SearchBar from "./SearchBar/searchBar";
import PlayControls from "./PlayControls/playControls";
import TrackTitle from "../TrackTitle/trackTitle";
import SeekBar from "./SeekBar/seekBar";
function MusicPlayer(props) {
  return (
    <>
      <TrackImage thumbnailUrl={props.thumbnailUrl} />
      <TrackTitle songState={props.songState} />
      <Center>
        <SeekBar track={props.trackTime} thumbnailUrl={props.thumbnailUrl} guildId={props.selectedServer}/>
      </Center>
      <PlayControls selectedServer={props.selectedServer} />
      <Center paddingBottom="20px">
        <SearchBar selectedServer={props.selectedServer} />
      </Center>
    </>
  );
}

export default MusicPlayer;
