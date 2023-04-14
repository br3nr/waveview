import { Center, Image } from "@chakra-ui/react";
import React from "react";

function ThumbnailImage({ thumbnailUrl }) {
    return (
      <Center>
        {thumbnailUrl && (
          <Image
            src={thumbnailUrl}
            fallbackSrc="/images/default.png"
            borderRadius='20px'
            objectFit="cover"
            objectPosition="center"
          />
        )}
      </Center>
    );
  }

export default ThumbnailImage;