import {
  Box,
  Flex,
  Avatar,
  Button,
  Menu,
  MenuButton,
  MenuList,
  useColorModeValue,
  Stack,
  useColorMode,
  Center,
} from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';
import React from 'react';
import { useRouter } from 'next/router';
import { BiLeftArrowAlt } from 'react-icons/bi'

export default function Nav(props) {
  const { colorMode, toggleColorMode } = useColorMode();
  const router = useRouter();

  function handleMenuClick() {
    router.push("/posts/server-select")
    setTimeout(() => {
      window.location.reload()
    }, 200)
  }

  return (
    <>
      <Box bg={useColorModeValue('gray.100', 'gray.900')} pl={2} pr={4}>
        <Flex h={16} alignItems={'center'} justifyContent={'space-between'}>
            <Button height="50px" width="50px" background="transparent" onClick={handleMenuClick}>
              <BiLeftArrowAlt />
            </Button>
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