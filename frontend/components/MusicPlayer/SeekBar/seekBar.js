import React from "react";
import { useState, useRef, useEffect } from "react";
import {
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
} from "@chakra-ui/react";
import { useCallback } from "react";

function SeekBar({ track }) {
  const [progress, setProgress] = useState(0.0);

  useEffect(() => {
    const progress = (parseInt(track[0]) / parseInt(track[1])) * 100;
    if (!isNaN(progress)) {
      setProgress(progress);
    }
  }, [track]);

  const handleChange = useCallback(
    async (value) => {
      const response = await fetch(
        `/seek/${localStorage.getItem("serverId")}/${track[1] * (value * 0.01)}`
      );
      if (response.ok) {
        setProgress(value);
      }
    },
    [track]
  );

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
          focusThumbOnChange={false}
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
