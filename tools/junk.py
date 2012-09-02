class PartAnimationSet:
	def test(self):
		for part_image in anim_dom.getElementsByTagName("part_image"):
			image = images[part_image.getAttribute("from")] #get image used
			#get source coordinate
			coord = [int(x.strip()) for x in part_image.getAttribute("coord").split(",")]
			surf = pygame.Surface((coord[2], coord[3]), SRCALPHA)
			surf.blit(image, (0, 0), coord)
			surfdata = pygame.image.tostring(surf, "RGBA", True)
			glBindTexture(GL_TEXTURE_2D, texnum)
			glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, coord[2], coord[3], 0, GL_RGBA, GL_UNSIGNED_BYTE, surfdata)
			glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
			if part_image.getAttribute("origin") != "": #if an origin was defined
				#get origin coord
				origin = [int(x.strip()) for x in part_image.getAttribute("origin").split(",")]
			else:
				origin = [0, 0]
			center = (surf.get_width()/2, surf.get_height()/2) #calculate new center
			self.part_images[part_image.getAttribute("id")] = (texnum, center, origin, (coord[2], coord[3])) #store created image
			texnum += 1