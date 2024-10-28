"""
For using OpenGL to render to an off screen buffer

Ref:
"""


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from OpenGL.GL import *
from OpenGL.raw.GL.VERSION import GL_1_1,GL_1_2, GL_3_0

class OffScreenRender(object):

    def __init__(self, width=1920, height=1080):
        super(OffScreenRender, self).__init__()
        self._width = width
        self._height = height
        self._fbo = None
        self._render_buf = None
        self._init_fbo()
        self._oldViewPort = (ctypes.c_int*4)*4

    def __enter__(self):
        self.activate()

    def __exit__(self, type, value, traceback):
        self.deactivate()
        return False

    def __del__(self):
        self._cleanup()
        super(OffScreenRender, self).__del__()

    def activate(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self._fbo)
        self._oldViewPort = glGetIntegerv(GL_VIEWPORT)
        side = min(self._width, self._height)
        glViewport(int((self._width - side)/2), int((self._height - side)/2), side, side)


    def deactivate(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(*self._oldViewPort)

    def read_into(self, buf, x=0, y=0, width=None, height=None):
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        width = width is not None or self._width,
        height = height is not None or self._height,
        glReadPixels(0,
                     0,
                     width,
                     height,
                     GL_BGRA,
                     #GL_RGBA, alot faster, but incorrect :()
                     GL_UNSIGNED_BYTE,
                     buf)
                     #outputType=None)
        #GL_1_1.glReadPixels(
        #    x,y,width,height,
        #    GL_BGRA,
        #    GL_UNSIGNED_BYTE,
        #    buf)


    def get_size(self):
        return self._width*self._height*4

    def _init_fbo(self, depth=True):
        fbo = glGenFramebuffers(1)
        self._fbo = fbo
        #  Could also use GL_READ_FRAMEBUFFER or GL_FRAMEBUFFER for both read
        #  and draw function calls.
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, fbo)

        render_buf = glGenRenderbuffers(1)
        self._render_buf = render_buf
        glBindRenderbuffer(GL_RENDERBUFFER, render_buf)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, self._width, self._height)
        glFramebufferRenderbuffer(GL_DRAW_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, render_buf)

        if depth:
            depth = glGenRenderbuffers(1)
            self._depth = depth
            glBindRenderbuffer(GL_RENDERBUFFER, depth)
            glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self._width, self._height)
            glBindRenderbuffer(GL_RENDERBUFFER, 0)
            glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth)

        assert GL_FRAMEBUFFER_COMPLETE  == glCheckFramebufferStatus(GL_DRAW_FRAMEBUFFER)

        glBindFramebuffer(GL_FRAMEBUFFER, 0);


    def _cleanup(self):
        if self._fbo is not None:
            glDeleteFramebuffers(self._fbo)
            self._fbo = None
        if self._render_buf is not None:
            glDeleteRenderbuffers(self._render_buf)
            self._render_buf = None



