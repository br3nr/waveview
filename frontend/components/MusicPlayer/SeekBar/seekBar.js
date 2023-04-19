import { Center, Box } from "@chakra-ui/react";
import React from "react";
import { useState, useEffect } from "react";

function SeekBar({ track, thumbnailUrl }) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    setProgress((track[0] / track[1]) * 100);
  }, [track]);

  useEffect(() => {
    setProgress((track[0] / track[1]) * 100);
  }, [track]);

  return (
   
      <Box
        w="80%"
        h="5px"
        bg="gray.900"
        borderRadius="full"
        position="relative"
      >
        <Box
          h="5px"
          bg="cyan.400"
          borderRadius="full"
          position="absolute"
          left={0}
          top={0}
          width={`${progress}%`}
          transition="width 0s linear"
        />
      </Box>

  );
}

export default SeekBar;
