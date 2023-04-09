import kaldi
model = kaldi.nnet3.NnetSimpleLoopedComputationOptions()
fst = fst.ReadFstKaldi("path/to/fst.txt")
decoder = decoder.Decoder(fst, model)

# Set up the decoder
decodable = online2.WavOnlineMatrixFeature(matrix.FloatMatrix())
decoder.InitDecoding()

# Decode the audio
result = decoder.DecodeSimple(decodable)