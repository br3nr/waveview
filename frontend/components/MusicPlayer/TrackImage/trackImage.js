import { Center, Image } from "@chakra-ui/react";
import React from "react";

function TrackImage({ thumbnailUrl }) {
  return (
    <Center>
      {thumbnailUrl && (
        <Image
          src={thumbnailUrl}
          borderRadius="20px"
          objectFit="cover"
          objectPosition="center"
          fallbackSrc=""
          height="500px"
          width="500px"
        />
      )}
    </Center>
  );
}

export default TrackImage;
