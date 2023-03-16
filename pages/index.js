import Head from 'next/head';
import styles from '../styles/Home.module.css';
import Link from 'next/link';
import Image from 'next/image';
import { ChakraProvider } from '@chakra-ui/react'


export default function Home() {
  return (
    <div className={styles.container}>
      <h1 className="title">
        <Link href="/posts/music-dashboard">Dashboard</Link>
      </h1>
      <h1 className="title">
        <Link href="/posts/test">Test Page</Link>
      </h1>
    </div>
  )
}
