import { Center, Box } from "@chakra-ui/react";
import React from "react";
import TrackImage from "./TrackImage/trackImage";
import SearchBar from "./SearchBar/searchBar";
import PlayControls from "./PlayControls/playControls";
import TrackTitle from "../TrackTitle/trackTitle";
import SeekBar from "./SeekBar/seekBar";
function MusicPlayer(props) {
  return (
    <>
      <Center>
        <SearchBar />
      </Center>
      <Box paddingTop={4}></Box>
      <TrackImage thumbnailUrl={props.thumbnailUrl} />
      <Box paddingTop={4}></Box>
      <TrackTitle songState={props.songState} />
      <Center paddingTop="10px" paddingBottom="10px">
        <SeekBar track={props.trackTime} />
      </Center>
      <PlayControls selectedServerId={props.selectedServerId} />
    </>
  );
}

export default MusicPlayer;
