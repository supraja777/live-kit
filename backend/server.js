import express from 'express';
import cors from 'cors';
import { AccessToken } from 'livekit-server-sdk';
import 'dotenv/config';

const app = express();
app.use(cors());
app.use(express.json());

app.get('/get-token', async (req, res) => {
  const { room, username } = req.query;

  if (!room || !username) {
    return res.status(400).send('Missing room or username');
  }

  const at = new AccessToken(
    process.env.LIVEKIT_API_KEY, 
    process.env.LIVEKIT_API_SECRET, 
    { identity: username }
  );

  at.addGrant({ roomJoin: true, room: room, agent: true });

  res.send({ token: await at.toJwt() });
});

app.listen(3001, () => console.log('Token server on port 3001'));