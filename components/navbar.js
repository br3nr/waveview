import { useState } from 'react';
import {
  Box,
  Flex,
  Avatar,
  Button,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useColorModeValue,
  Stack,
  useColorMode,
  Text,
  Center,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';
import React from 'react';
import { useRouter } from 'next/router';

export default function Nav(props) {
  const { colorMode, toggleColorMode } = useColorMode();
  const [serverList, setServerList] = useState([{}]);
  const [serverIcon, setServerIcon] = useState("https://www.svgrepo.com/show/353655/discord-icon.svg");
  const router = useRouter();

  const [currentPath, setCurrentPath] = useState(router.pathname);

  const handleHomeClick = () => {
    // TODO: Make this a link to the home page
  };
  
  return (
    <>
      <Box bg={useColorModeValue('gray.100', 'gray.900')} px={4}>
        <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
          <Menu>
            <MenuButton
              as={Button}
              variant={'link'}
              cursor={'pointer'}
              onClick={handleHomeClick}
              minW={0}
              key={currentPath}>
              <Avatar
                size={'sm'}
                src={serverIcon}
              />
            </MenuButton> 
          </Menu>
          <Flex alignItems={'center'}>
            <Stack direction={'row'} spacing={7}>
              <Button onClick={toggleColorMode}>
                {colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
              </Button>
              <Menu>
                <MenuButton
                  as={Button}
                  rounded={'full'}
                  variant={'link'}
                  cursor={'pointer'}
                  minW={0}>
                  <Avatar
                    size={'sm'}
                    src={props.currentUser.avatar_url}
                  />
                </MenuButton>
                <MenuList alignItems={'center'}>
                  <br />
                  <Center>
                    <Avatar
                      size={'2xl'}
                      src={props.currentUser.avatar_url}
                    />
                  </Center>
                  <br />
                  <Center>
                    <p>{props.currentUser.username}</p>
                  </Center>
                  <br />
                </MenuList>
              </Menu>
            </Stack>
          </Flex>
        </Flex>
      </Box>
    </>
  );
}