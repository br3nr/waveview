import { Center, Box } from "@chakra-ui/react";
import React from "react";
import { useState, useEffect } from "react";
import {
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  SliderMark,
} from "@chakra-ui/react";
import { BsX } from "react-icons/bs";

function SeekBar({ track, thumbnailUrl, guildId }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    setProgress((track[0] / track[1]) * 100);
  }, [track]);

  const handleChange = async (value) => {
    const response = await fetch(
      `/seek/${guildId}/${track[1] * (value * 0.01)}`
    );
    if (response.ok) {
      setProgress(value);
    }
  };

  return (
    <>
      {!(track[1] === 0) ? (
        <Slider
          aria-label="slider-ex-3"
          width="80%"
          defaultValue={0}
          value={progress}
          minH="1"
          onChange={(value) => handleChange(value)}
        >
          <SliderTrack bg="gray.900">
            <SliderFilledTrack bg="red" />
          </SliderTrack>
          <SliderThumb />
        </Slider>
      ) : (
        <Slider
          aria-label="slider-ex-3"
          width="80%"
          defaultValue={0}
          minH="1"
        />
      )}
    </>
  );
}

export default SeekBar;
