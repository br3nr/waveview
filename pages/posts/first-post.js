import Link from 'next/link';
import Script from 'next/script';
import Layout from '../../components/layout';
import Image from 'next/image';
import { useState, useEffect } from 'react';


function FirstPost() {

	const [thumbnailUrl, setThumbnailUrl] = useState(null)

  useEffect(() => {
    const fetchThumbnail = async () => {
      const response = await fetch('/thumbnail')
      const data = await response.json()
      setThumbnailUrl(data.thumbnailUrl)
    }
    fetchThumbnail()
  }, [])


	return (
		<>
			<h1>First Post</h1>
			{thumbnailUrl && (
        <Image
          src={thumbnailUrl}
          alt="Thumbnail image for YouTube video"
          width={640}
          height={360}
        />
      )}
			<h2>
				<Link href="/">Back to home</Link>
			</h2>
		</>
	);
}

export default FirstPost;