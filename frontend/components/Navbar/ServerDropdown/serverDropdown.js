import { Image, Menu, MenuButton, MenuItem, MenuList, Button } from "@chakra-ui/react";
import React from "react";
import { useState, useEffect } from "react";

function ServerDropdown({serverList, setSelectedServer}) {

  useEffect(() => {}, []);

  return (
    <>
      <Menu>
        <MenuButton  w="40px" h="40px" bgImage="/discord.png" bgSize="40px" as={Button}>
        </MenuButton>
        <MenuList>
          <MenuItem minH="48px">
            <Image
              boxSize="2rem"
              borderRadius="full"
              src=""
              mr="12px"
            />
            <span>Server Here</span>
          </MenuItem>
          <MenuItem minH="40px">
            <Image
              boxSize="2rem"
              borderRadius="full"
              src=""
              mr="12px"
            />
            <span>Server Here</span>
          </MenuItem>
        </MenuList>
      </Menu>
    </>
  );
}

export default ServerDropdown;
