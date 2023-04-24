import { Center } from "@chakra-ui/react";
import React from "react";
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
        <SeekBar track={props.trackTime} />
      </Center>
      <PlayControls selectedServerId={props.selectedServerId} />
      <Center paddingBottom="20px">
        <SearchBar />
      </Center>
    </>
  );
}

export default MusicPlayer;
