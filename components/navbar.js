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

export default function Nav(props) {
  const { colorMode, toggleColorMode } = useColorMode();
  const [serverList, setServerList] = useState([{}]);
  const [serverIcon, setServerIcon] = useState("https://www.svgrepo.com/show/353655/discord-icon.svg");

  function handleServerClick(server) {
    props.handleServerClick(server);
    setServerIcon(server.icon);
  }

  async function onMenuClick() {
    const response = await fetch("/get_servers");
    const data = await response.json();
    setServerList(data);
    console.log(data)
  }

  return (
    <>
      <Box bg={useColorModeValue('gray.100', 'gray.900')} px={4}>
        <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
          <Menu>
            <MenuButton
              as={Button}
              variant={'link'}
              cursor={'pointer'}
              onClick={onMenuClick}
              minW={0}>
              <Avatar
                size={'sm'}
                src={serverIcon}
              />
            </MenuButton>
            <MenuList alignItems={'center'}>
              <Text paddingLeft={5} paddingTop={3}>Available Servers:</Text>
              {serverList?.map((server) => (
                <Flex key={server.name} borderRadius="50px" alignItems="center" width={350} margin="10px" >
                  <MenuItem >
                    <Text onClick={() => handleServerClick(server)} >{server.name}</Text>
                  </MenuItem>
                </Flex>
              ))}
            </MenuList>
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
                    src={'https://static1.personality-database.com/profile_images/4097d505c488482688656aad6cd03992.png'}
                  />
                </MenuButton>
                <MenuList alignItems={'center'}>
                  <br />
                  <Center>
                    <Avatar
                      size={'2xl'}
                      src={'https://static1.personality-database.com/profile_images/4097d505c488482688656aad6cd03992.png'}
                    />
                  </Center>
                  <br />
                  <Center>
                    <p>m4x</p>
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